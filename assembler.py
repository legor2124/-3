#!/usr/bin/env python3
import sys
import os
from uvm_core import Opcode, Command

class Assembler:
    """Ассемблер УВМ"""
    
    def __init__(self):
        self.commands: list[Command] = []
    
    def parse_line(self, line: str) -> Command:
        """Парсинг строки ассемблера"""
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith(';'):
            return None
        
        # Удаляем комментарий в конце строки
        if ';' in line:
            line = line.split(';')[0].strip()
        
        parts = line.split()
        if not parts:
            return None
        
        mnemonic = parts[0].upper()
        
        # Парсинг аргументов
        args_str = ' '.join(parts[1:])
        args = []
        for arg in args_str.split(','):
            arg = arg.strip()
            if arg:
                try:
                    # Поддержка шестнадцатеричных чисел
                    if arg.startswith('0x'):
                        args.append(int(arg, 16))
                    else:
                        args.append(int(arg))
                except ValueError:
                    raise ValueError(f"Invalid argument: {arg}")
        
        # Преобразование мнемоники в код операции
        opcode_map = {
            'LOAD_CONST': Opcode.LOAD_CONST,
            'READ_MEM': Opcode.READ_MEM,
            'WRITE_MEM': Opcode.WRITE_MEM,
            'SHR': Opcode.SHR
        }
        
        if mnemonic not in opcode_map:
            raise ValueError(f"Unknown instruction: {mnemonic}")
        
        # Проверка количества аргументов
        expected_args = {
            Opcode.LOAD_CONST: 2,
            Opcode.READ_MEM: 2,
            Opcode.WRITE_MEM: 2,
            Opcode.SHR: 2
        }
        
        if len(args) != expected_args[opcode_map[mnemonic]]:
            raise ValueError(
                f"Instruction {mnemonic} expects {expected_args[opcode_map[mnemonic]]} arguments, "
                f"got {len(args)}"
            )
        
        # Проверка диапазонов аргументов
        if mnemonic == 'LOAD_CONST':
            reg, const = args
            if not (0 <= reg <= 31):
                raise ValueError(f"Register number must be 0-31, got {reg}")
            if not (0 <= const <= 0xFFFFFF):
                raise ValueError(f"Constant must be 0-16777215, got {const}")
        
        elif mnemonic in ('READ_MEM', 'WRITE_MEM'):
            reg1, reg2 = args
            if not (0 <= reg1 <= 31) or not (0 <= reg2 <= 31):
                raise ValueError(f"Register numbers must be 0-31, got {reg1}, {reg2}")
        
        elif mnemonic == 'SHR':
            reg, addr = args
            if not (0 <= reg <= 31):
                raise ValueError(f"Register number must be 0-31, got {reg}")
            if not (0 <= addr <= 0x3FFFFFFF):
                raise ValueError(f"Memory address must be 0-1073741823, got {addr}")
        
        return Command(opcode_map[mnemonic], args)
    
    def assemble(self, source_path: str, output_path: str, test_mode: bool = False):
        """Основной метод ассемблирования"""
        with open(source_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        self.commands.clear()
        line_num = 0
        
        for line in lines:
            line_num += 1
            try:
                cmd = self.parse_line(line)
                if cmd:
                    self.commands.append(cmd)
            except ValueError as e:
                print(f"Error at line {line_num}: {e}")
                print(f"  Line: {line.strip()}")
                if not test_mode:
                    sys.exit(1)
        
        # Генерация бинарного кода
        binary_data = b''
        for cmd in self.commands:
            binary_data += cmd.to_binary()
        
        # Запись в файл
        with open(output_path, 'wb') as f:
            f.write(binary_data)
        
        # Вывод информации
        print(f"Assembled {len(self.commands)} commands")
        print(f"Output file size: {len(binary_data)} bytes")
        
        if test_mode:
            print("\nIntermediate representation:")
            for i, cmd in enumerate(self.commands):
                print(f"{i:3d}: {cmd}")
            
            print("\nBinary output:")
            offset = 0
            for cmd in self.commands:
                binary = cmd.to_binary()
                hex_str = ' '.join(f'{b:02x}' for b in binary)
                print(f"{offset:04x}: {hex_str}")
                offset += len(binary)

def main():
    if len(sys.argv) < 3:
        print("Usage: python assembler.py <input.asm> <output.bin> [test]")
        print("Example: python assembler.py program.asm program.bin test")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = len(sys.argv) > 3 and sys.argv[3].lower() == 'test'
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        sys.exit(1)
    
    assembler = Assembler()
    try:
        assembler.assemble(input_file, output_file, test_mode)
        print(f"Successfully assembled {input_file} to {output_file}")
    except Exception as e:
        print(f"Assembly failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
