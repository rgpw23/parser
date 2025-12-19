import unittest
from parser import Parser  

class TestParser(unittest.TestCase):
    
    def test_simple_dict(self):
        text = 'NAME = 42;'
        parser = Parser(text)
        result = parser.parse()  
        self.assertEqual(result, {'NAME': 42})
    
    def test_string(self):
        text = 'MSG = "Hello";'
        parser = Parser(text)
        result = parser.parse()  
        self.assertEqual(result, {'MSG': 'Hello'})
    
    def test_nested_dict(self):
        text = '''
        
            PORT = 8080;
            HOST = "localhost";
    
        '''
        parser = Parser(text)
        result = parser.parse()  
        self.assertEqual(result, {'PORT': 8080, 'HOST': 'localhost'})
    
    def test_scientific_notation(self):
        text = 'VAL = 1.2e+3;'
        parser = Parser(text)
        result = parser.parse() 
        self.assertEqual(result, {'VAL': 1200.0})

if __name__ == '__main__':
    unittest.main()