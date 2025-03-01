# :mag: GitHub Action Check Source to Target Difference

> A GitHub Action to check and identify differences between source and target directories, helping track changes across content variants.

## :question: Why use this GitHub Action?

Maintaining synchronized content across multiple directories (such as different language variants) can be challenging.
This GitHub Action automates the process by comparing directories and providing structured output for further processing.

## About

This action analyzes differences between a source directory and a target directory across git references. It identifies new files, modified files, and deleted files, making it perfect for translation workflows or any process where content synchronization is required. 

## Usage

>:white_flag: See the [inputs](#inputs) section for detailed descriptions.

```yaml
- name: Check Source to Target Difference
  id: check_difference
  uses: KevinRohn/action-compare-directory@v0.1.1
  with:
    source_dir: "content/en"
    target_dir: "content/de"
    from_ref: ${{ github.event.before }}
    to_ref: ${{ github.event.after }}
```

## Usage examples

Basic comparison between language directories

```yaml
- name: Compare English and German content
  id: compare_en_de
  uses: KevinRohn/action-compare-directory@v0.1.1
  with:
    source_dir: "content/en"
    target_dir: "content/de"
    from_ref: ${{ github.event.before }}
    to_ref: ${{ github.event.after }}
```

## Inputs

The action supports the following inputs:

- `source_dir`
  The source directory to compare against the target.
  **Required:** *true*

- `target_dir`
  The target directory to compare with the source.
  **Required:** *true*

- `from_ref`
  The git reference to compare from (usually an older commit).
  **Required:** *true*

- `to_ref`
  The git reference to compare to (usually the current commit).
  **Required:** *true*

## Outputs

- `new_files`
  JSON array of objects containing source and target paths for new files that exist in the source directory but not in the target directory.

- `modified_files`
  JSON array of objects containing source and target paths for files that exist in both directories but have been modified in the source directory.

- `deleted_files`
  JSON array of objects containing source and target paths for files that have been deleted from the source directory but still exist in the target directory.

### Output Format

Each output is a JSON array with objects in the following format:

```json
[
  {
    "source": "path/to/source/file.md",
    "target": "path/to/target/file.md"
  }
]
```

### Processing outputs

```yaml
- name: Process New Files
  if: ${{ steps.compare.outputs.new_files != '[]' }}
  run: |
    echo '${{ steps.compare.outputs.new_files }}' | jq -c '.[]' | while read -r file; do
      SOURCE=$(echo "$file" | jq -r '.source')
      TARGET=$(echo "$file" | jq -r '.target')
      echo "New file - Source: $SOURCE, Target: $TARGET"
      # Add your processing logic here
    done
```