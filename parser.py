import sys
import re
import json
from typing import Any, Dict, List, Union

class Parser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.constants: Dict[str, Any] = {}
        self.tokens = self.tokenize()


    def tokenize(self) -> List[str]:
        """Разбивает текст на токены."""
        text = self.text
        

        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if '\\' in line:
                line = line.split('\\')[0]
            cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
        

        while '(comment' in text:
            start = text.find('(comment')
            end = text.find(')', start)
            if end == -1:
                break
            text = text[:start] + text[end+1:]
        

        tokens = []
        i = 0
        while i < len(text):
  
            if text[i].isspace():
                i += 1
                continue
            

            if text[i] == '"':
                end = text.find('"', i + 1)
                if end == -1:
                    raise SyntaxError('Незакрытая строка')
                tokens.append(text[i:end+1])
                i = end + 1
                continue
            
          
            if text[i] in '{}=;':
                tokens.append(text[i])
                i += 1
                continue
            
       
            start = i
            while i < len(text) and not text[i].isspace() and text[i] not in '{}=;"':
                i += 1
            token = text[start:i]
            if token:
                tokens.append(token)
        
        return tokens

    def parse_value(self) -> Any:
        """Парсит значение (число, строку, словарь)."""
        if not self.tokens:
            raise SyntaxError('Ожидается значение')
        
        token = self.tokens[0]
        
        
     
        if token == '{':
            self.tokens.pop(0)  
            return self.parse_dict()
        
 
        elif token.lower() == 'true':
            self.tokens.pop(0)
            return True
        elif token.lower() == 'false':
            self.tokens.pop(0)
            return False
        
        
        elif token.startswith('"'):
            self.tokens.pop(0)
            return token[1:-1]
        
       
        else:
            self.tokens.pop(0)
            
         
            if re.match(r'^[+-]?\d+\.?\d*[eE][+-]?\d+$', token):
                return float(token)
       
            elif re.match(r'^[+-]?\d+$', token):
                return int(token)
            elif re.match(r'^[+-]?\d+\.\d*$', token):
                return float(token)

            elif re.match(r'^[A-Z]+$', token):
                if token in self.constants:
                    return self.constants[token]
                else:
                    raise NameError(f'Константа "{token}" не определена')
            else:
                raise SyntaxError(f'Неизвестный токен: {token}')

    def parse(self) -> Dict[str, Any]:

        result = {}
        

        temp_tokens = self.tokens.copy()
        i = 0
        while i < len(temp_tokens):
            if (i + 2 < len(temp_tokens) and
                re.match(r'^[A-Z]+$', temp_tokens[i]) and
                temp_tokens[i+1] == '=' and
                temp_tokens[i+2] not in ['{', ';']):
                
                name = temp_tokens[i]
                value_token = temp_tokens[i+2]
                
 
                if re.match(r'^[+-]?\d+\.?\d*[eE][+-]?\d+$', value_token):
                    self.constants[name] = float(value_token)
                elif re.match(r'^[+-]?\d+$', value_token):
                    self.constants[name] = int(value_token)
                elif value_token.startswith('"'):
                    self.constants[name] = value_token[1:-1]
                elif value_token.lower() == 'true':
                    self.constants[name] = True
                elif value_token.lower() == 'false':
                    self.constants[name] = False
                
                i += 4 if i+3 < len(temp_tokens) and temp_tokens[i+3] == ';' else 3
            else:
                i += 1
        
        i = 0
        while i < len(self.tokens):
            if self.tokens[i] == ';':
                i += 1
                continue
            
            if self.tokens[i] == '{':

                i += 1
           
                while i < len(self.tokens) and self.tokens[i] != '}':
                    i += 1
                if i < len(self.tokens):
                    i += 1  
            else:
  
                if (i + 2 < len(self.tokens) and
                    re.match(r'^[A-Z]+$', self.tokens[i]) and
                    self.tokens[i+1] == '='):
                    
                    key = self.tokens[i]
                    value_token = self.tokens[i+2]
                    
          
                    if value_token in self.constants:
                        value = self.constants[value_token]
                    elif value_token.startswith('"'):
                        value = value_token[1:-1]
                    elif re.match(r'^[+-]?\d+\.?\d*[eE][+-]?\d+$', value_token):
                        value = float(value_token)
                    elif re.match(r'^[+-]?\d+$', value_token):
                        value = int(value_token)
                    elif value_token.lower() == 'true':
                        value = True
                    elif value_token.lower() == 'false':
                        value = False
                    else:
                        value = value_token
                    
                    result[key] = value
                    
                    i += 4 if i+3 < len(self.tokens) and self.tokens[i+3] == ';' else 3
                else:
                    i += 1
    
        return result


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Использование: python3 parser.py < input.conf > output.json")
        print("Пример: echo 'PORT = 8080;' | python3 parser.py")
        sys.exit(0)

    input_text = sys.stdin.read()
    parser = Parser(input_text)
    try:
        result = parser.parse()
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    except (SyntaxError, NameError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()