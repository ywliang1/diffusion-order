from huggingface_hub import snapshot_download
import sys
repo,rev=sys.argv[1:]
print(snapshot_download(repo_id=repo, revision=rev, local_dir=f'weights/{repo.split("/")[1]}', ignore_patterns=['*.md','*.png','*.jpg','.gitattributes'], max_workers=4), flush=True)
