import json
import sys
import os
import io
import traceback

nb_path = r'D:\ex_work\AirQualityReview_Project\validation_docs\Validation_Test_Execution.ipynb'
sys.path.insert(0, r'D:\ex_work\AirQualityReview_Project')

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Global dictionary to maintain state across cell executions
global_ns = {
    'display': lambda x: print(x.to_string() if hasattr(x, 'to_string') else x)
}

# Execute all cells in order
for idx, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source_code = ''.join(cell['source'])
        print(f"Executing cell {idx}...")
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        error_occurred = False
        ename, evalue, tb_list = "", "", []
        
        try:
            exec(source_code, global_ns)
        except Exception as e:
            error_occurred = True
            ename = type(e).__name__
            evalue = str(e)
            tb_list = traceback.format_exception(*sys.exc_info())
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
        stdout_val = stdout_capture.getvalue()
        stderr_val = stderr_capture.getvalue()
        
        outputs = []
        if stdout_val:
            # Format lines to end with \n as Jupyter expects
            lines = [line + '\n' for line in stdout_val.split('\n')][:-1]
            if stdout_val.endswith('\n'):
                lines.append('\n') if not lines or lines[-1] != '\n' else None
            else:
                if lines:
                    lines[-1] = lines[-1].rstrip('\n')
            outputs.append({
                "name": "stdout",
                "output_type": "stream",
                "text": stdout_val.splitlines(keepends=True)
            })
            
        if stderr_val:
            outputs.append({
                "name": "stderr",
                "output_type": "stream",
                "text": stderr_val.splitlines(keepends=True)
            })
            
        if error_occurred:
            outputs.append({
                "ename": ename,
                "evalue": evalue,
                "output_type": "error",
                "traceback": tb_list
            })
            print(f"Error in cell {idx}: {evalue}")
            
        cell['outputs'] = outputs
        cell['execution_count'] = idx

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook execution and save completed successfully.")
