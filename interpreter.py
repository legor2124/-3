#!/usr/bin/env python3
import sys
import os
import csv
from uvm_core import VirtualMachine

class Interpreter:
    """Интерпретатор УВМ"""
    
    def __init__(self):
        self.vm = VirtualMachine()
    
    def load_and_run(self, binary_path: str, dump_path: str = None, 
                     mem_start: int = 0, mem_end: int = 100):
        """Загрузка и выполнение программы"""
        
        # Загрузка бинарного файла
        with open(binary_path, 'rb') as f:
            binary_data = f.read()
        
        print(f"Loaded {len(binary_data)} bytes from {binary_path}")
        
        # Загрузка программы в ВМ
        self.vm.load_program(binary_data)
        print(f"Program has {len(self.vm.program)} commands")
        
        # Выполнение программы
        print("Executing program...")
        self.vm.run()
        print("Program execution completed")
        
        # Вывод состояния регистров
        print("\nRegister states:")
        for i in range(0, 32, 8):
            regs = self.vm.registers[i:i+8]
            reg_nums = [f"R{j:02d}" for j in range(i, i+8)]
            values = [f"{v:08x}" for v in regs]
            print(f"{' '.join(reg_nums)}: {' '.join(values)}")
        
        # Сохранение дампа памяти
        if dump_path:
            self.save_memory_dump(dump_path, mem_start, mem_end)
        
        return self.vm
    
    def save_memory_dump(self, dump_path: str, start_addr: int, end_addr: int):
        """Сохранение дампа памяти в CSV"""
        dump = self.vm.dump_memory(start_addr, end_addr)
        
        with open(dump_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Address', 'Value (dec)', 'Value (hex)'])
            for addr, value in dump:
                writer.writerow([addr, value, f"0x{value:08x}"])
        
        print(f"Memory dump saved to {dump_path} (addresses {start_addr}-{end_addr})")
        
        # Вывод первых нескольких строк дампа
        print("\nFirst 10 memory values:")
        for i, (addr, value) in enumerate(dump[:10]):
            print(f"  0x{addr:04x}: {value:8d} (0x{value:08x})")

def main():
    if len(sys.argv) < 3:
        print("Usage: python interpreter.py <program.bin> <dump.csv> <start-end>")
        print("Example: python interpreter.py program.bin dump.csv 0-100")
        sys.exit(1)
    
    binary_file = sys.argv[1]
    dump_file = sys.argv[2]
    
    if len(sys.argv) >= 4:
        addr_range = sys.argv[3]
        try:
            start_str, end_str = addr_range.split('-')
            mem_start = int(start_str)
            mem_end = int(end_str)
        except ValueError:
            print("Invalid address range format. Use: start-end (e.g., 0-100)")
            sys.exit(1)
    else:
        mem_start = 0
        mem_end = 100
    
    if not os.path.exists(binary_file):
        print(f"Binary file not found: {binary_file}")
        sys.exit(1)
    
    interpreter = Interpreter()
    try:
        interpreter.load_and_run(binary_file, dump_file, mem_start, mem_end)
    except Exception as e:
        print(f"Interpretation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
