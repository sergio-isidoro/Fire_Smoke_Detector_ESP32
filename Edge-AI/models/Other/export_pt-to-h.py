import sys
import torch
import io

if len(sys.argv) != 3:
    print("Uso: python convert_model.py model.pt model.h")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# Carrega o state_dict (ou modelo completo, se for o caso)
state_dict = torch.load(input_file, map_location='cpu')

# Serializa para bytes usando BytesIO
buffer = io.BytesIO()
torch.save(state_dict, buffer)
byte_array = bytearray(buffer.getvalue())

# Converte para array C
with open(output_file, 'w') as f:
    f.write('#ifndef MODEL_H\n#define MODEL_H\n\n')
    f.write('const unsigned char model_data[] = {')
    f.write(','.join(str(b) for b in byte_array))
    f.write('};\n')
    f.write('const unsigned int model_data_len = {};\n'.format(len(byte_array)))
    f.write('\n#endif // MODEL_H\n')

print(f"Arquivo {output_file} gerado com sucesso!")
