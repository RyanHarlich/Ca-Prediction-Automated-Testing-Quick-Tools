import argparse
import get_experimental_data as this
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get and save experimental map and ground truth')
    parser.add_argument('output', type=str, help='Name of output folder')
    parser.add_argument('emdb_id', type=str, help='ID of experimental density map')
    parser.add_argument('pdb_id', type=str, help='ID of experimental PDB ground truth')
    parser.add_argument('-c', '--chain', metavar='Chain', type=str, help='Specified chain')
    parser.add_argument('-a', '--align', action='store_const', const=True, default=False, help='Align structure and density map that are not already aligned')
    args = parser.parse_args()

    args.output += '/' if args.output[-1] != '/' else ''
    args.output = os.getcwd().replace(os.sep, '/') + '/' + args.output

    this.run(args.output, args.emdb_id, args.pdb_id, args.chain, args.align)

def run(output_path, emdb_id, pdb_id, chain, align):
    cwd = os.getcwd().replace(os.sep,'/') + '/'
    chimera_script = open(cwd + 'chimera_script.cmd', 'w')
    if chain is not None:
        output_path += emdb_id + chain
    else:
        output_path += emdb_id
    os.makedirs(output_path, exist_ok=True)

    if chain is None:
        if align is False:
            chimera_script.write('open emdbID:' + emdb_id + '\n'
                                 'open ' + pdb_id + '\n'
                                 'write #1 ' + output_path + '/' + pdb_id + '.ent\n'
                                 'volume #0 save ' + output_path + '/' + emdb_id + '.mrc')
        else:
            chimera_script.write('open emdbID:' + emdb_id + '\n'
                                 'cofr models\n'
                                 'cofr fixed\n'
                                 'open ' + pdb_id + '\n'
                                 'move cofr mod #1\n'
                                 'write relative #0 #1 ' + output_path + '/' + pdb_id + '.ent\n'
                                 'volume #0 save ' + output_path + '/' + emdb_id + '.mrc')
    else:
        if align is False:
            chimera_script.write('open emdbID:' + emdb_id + '\n'
                                 'open ' + pdb_id + '\n'
                                 'select #1 :.' + chain + '\n'
                                 'select invert sel\n'
                                 'delete sel\n'
                                 'sop zone #0 #1 4\n'                            
                                 'write #1 ' + output_path + '/' + pdb_id + '.ent\n'
                                 'volume #0 save ' + output_path + '/' + emdb_id + '.mrc')
        else:
            chimera_script.write('open emdbID:' + emdb_id + '\n'
                                 'cofr models\n'
                                 'cofr fixed\n'
                                 'open ' + pdb_id + '\n'
                                 'move cofr mod #1\n'
                                 'select #1 :.' + chain + '\n'
                                 'select invert sel\n'
                                 'delete sel\n'
                                 'sop zone #0 #1 4\n'                            
                                 'write relative #0 #1 ' + output_path + '/' + pdb_id + '.ent\n'
                                 'volume #0 save ' + output_path + '/' + emdb_id + '.mrc')

    chimera_script.close()
    os.system('C:/"Program Files"/"Chimera 1.13.1"/bin/chimera --nogui ' + chimera_script.name)
    os.remove(chimera_script.name)