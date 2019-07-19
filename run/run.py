import partial_protein.partial_protein as partial
import score.score_phenix as score
import os
import sys
from multiprocessing import cpu_count, Pool
import traceback
#from .evaluate import build_excel
from .evaluate import Evaluator

__author__ = 'Michael Ryan Harlich'

PIPELINE = [
    partial,
    score
]

def run(input_path, output_path, selections_file, phenix_path, tmalign_path):
    params_list = [(emdb_id, input_path, output_path, selections_file, phenix_path, tmalign_path) 
                   for emdb_id in filter(lambda d: os.path.isdir(input_path + d), os.listdir(input_path))]

    # Use with caution
    #os.system("rm " + output_path + "* -r")

    pool = Pool(min(cpu_count(), len(params_list)))
    results = pool.map(run_steps, params_list)

    #params_list.sort(key=lambda tup: tup[0])
    #build_excel(output_path, params_list, selections_file)
    results = filter(lambda r: r is not None, results)
    inputpath_blank = ""
    evaluator = Evaluator(inputpath_blank)
    for emdb_id, predicted_file, gt_file, execution_time in results:
        evaluator.evaluate(emdb_id, predicted_file, gt_file, execution_time)

    evaluator.create_report(output_path, 0)




def run_steps(params):
    emdb_id, input_path, output_path, selections_file, phenix_path, tmalign_path = params
    paths = make_paths(input_path, emdb_id, selections_file, phenix_path, tmalign_path)

    for step in PIPELINE:
        paths['output'] = output_path + emdb_id + '/' + step.__name__.split('.')[0] + '/'
        os.makedirs(paths['output'], exist_ok=True)
        try:
            step.update_paths(paths)
            step.execute(paths)
        except:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)

    # NOTE: This should eventually be aligned_prediction (whole)
    return emdb_id, paths['prediction'], paths['partial_ground_truth'], 0


def make_paths(input_path, emdb_id, selections_file, phenix_path, tmalign_path):
    prediction_file = get_file(input_path + emdb_id, ['pdb', 'ent'])
    gt_file = get_file(input_path + emdb_id, ['pdb', 'ent'], ['native'])
    paths = {
        'prediction': input_path + emdb_id + '/' + prediction_file,
        'ground_truth': input_path + emdb_id + '/' + gt_file
    }

    if selections_file is not None:
        paths['selections_file'] = selections_file
    if phenix_path is not None:
        paths['phenix_chain_comparison_path'] = phenix_path
    if tmalign_path is not None:
        paths['tmalign_path'] = tmalign_path

    return paths


def get_file(path, allowed_extensions, filename=None):
    if filename is None:
        file = next(f for f in os.listdir(path) if f.split('.')[-1] in allowed_extensions and f.split('.')[0] not in ['native'])
    else:
        file = next(f for f in os.listdir(path) if f.split('.')[-1] in allowed_extensions and f.split('.')[0] in filename)
    return file
    
    
