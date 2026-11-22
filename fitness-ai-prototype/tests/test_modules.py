import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
# Lightweight SDK stubs allow unit tests without installing the real SDK.
# Actual API calls still require google-genai from requirements.txt.
import sys
import types as pytypes
try:
    from google import genai as _genai
except ImportError:
    google = pytypes.ModuleType('google')
    google.__path__ = []
    sdk = pytypes.ModuleType('google.genai')
    sdk.types = pytypes.SimpleNamespace(Part=pytypes.SimpleNamespace(from_bytes=lambda **kw: kw))
    sdk.errors = pytypes.SimpleNamespace(APIError=type('APIError', (Exception,), {}))
    google.genai = sdk
    sys.modules['google'] = google
    sys.modules['google.genai'] = sdk

from ai.context import missing_fields, fitness_ai
from ai.workout import validate_workout, generate_workout
from ai.nutrition import generate_nutrition
from ai.rag import retrieve, answer_with_sources
from ai.food_vision import analyze_food_image
from ai.speech import transcribe_audio

PROFILE = {'goal':'muscle_gain','experience':'beginner','days_per_week':2,'minutes_per_session':45,'equipment':['dumbbells'],'physical_limitations':'none reported'}

class ModuleTests(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(missing_fields({'goal':'muscle_gain'}), ['experience','days_per_week','minutes_per_session','equipment'])
    @patch('ai.context.generate', return_value={'type':'chat','message':'2 buổi','missing_fields':[],'proposed_profile_updates':{}})
    def test_context(self, mock):
        self.assertEqual(fitness_ai('Tập mấy buổi?', PROFILE, [])['message'], '2 buổi')
        self.assertIn('days_per_week', mock.call_args.args[0])
    def test_workout_validation(self):
        p = {'sessions':[{'exercises':[{'name':'Floor Press','sets':3,'reps':'8-12','rest_seconds':90}]}]}
        self.assertIn('session count differs from days_per_week', validate_workout(p, PROFILE))
    @patch('ai.workout.generate')
    def test_workout(self, mock):
        mock.return_value = {'type':'workout_plan','sessions':[{'exercises':[{'name':'Floor Press','sets':3,'reps':'8-12','rest_seconds':90}]},{'exercises':[{'name':'Squat','sets':3,'reps':'8-12','rest_seconds':90}]}]}
        self.assertEqual(generate_workout(PROFILE)['type'], 'workout_plan')
    def test_workout_clarification(self):
        p = dict(PROFILE, physical_limitations=None)
        self.assertEqual(generate_workout(p)['type'], 'clarification')
    @patch('ai.nutrition.generate', return_value={'type':'nutrition_advice','message':'Ăn đa dạng','suggestions':[],'missing_fields':[],'sample_day':[]})
    def test_nutrition(self, mock):
        self.assertEqual(generate_nutrition(PROFILE)['type'], 'nutrition_advice')
    def test_retrieval(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'guide.txt').write_text('Protein and resistance exercise can support muscle adaptation.', encoding='utf-8')
            self.assertEqual(retrieve('protein muscle', d)[0]['source'], 'guide.txt')
    @patch('ai.rag.generate', return_value={'type':'rag_answer','message':'Có nguồn','sources':[{'source':'guide.txt','chunk':0},{'source':'fake.txt','chunk':0}]})
    def test_rag_sources(self, mock):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'guide.txt').write_text('Protein and resistance exercise support muscle adaptation.', encoding='utf-8')
            result = answer_with_sources('protein muscle', d)
            self.assertEqual(len(result['sources']), 1)
    def test_missing_image(self):
        with self.assertRaises(FileNotFoundError): analyze_food_image('missing.jpg')
    def test_missing_audio(self):
        with self.assertRaises(FileNotFoundError): transcribe_audio('missing.wav')

if __name__ == '__main__':
    unittest.main()
