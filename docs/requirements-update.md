# Automatic Requirements Update in PyCharm

This document explains how the automatic update of `requirements.txt` and `dev-requirements.txt` works in this project.

## How It Works

When you open the project in PyCharm, a startup task automatically runs the `generate_requirements.sh` script, which:

1. Updates `requirements.txt` with all project dependencies from Poetry
2. Updates `dev-requirements.txt` with development dependencies from Poetry

This ensures that both requirements files are always up-to-date with the dependencies defined in `pyproject.toml` and locked in `poetry.lock`.

## Configuration Files

The automatic update is configured through two PyCharm configuration files:

1. `.idea/runConfigurations/Generate_Requirements.xml` - Defines the run configuration for the script
2. `.idea/startup-tasks.xml` - Configures the run configuration to execute on project startup

## Manual Update

If you need to manually update the requirements files, you can:

1. Run the `generate_requirements.sh` script directly from the terminal:
   ```bash
   ./generate_requirements.sh
   ```

2. Run the "Generate Requirements" run configuration from within PyCharm:
   - Open the Run/Debug Configurations dropdown
   - Select "Generate Requirements"
   - Click the Run button

## Troubleshooting

If the automatic update doesn't work:

1. Make sure the `.idea` directory is included in your project
2. Check that the run configuration is properly set up in PyCharm
3. Verify that the startup task is enabled in PyCharm settings:
   - Go to Settings → Tools → Startup Tasks
   - Ensure "Generate Requirements" is checked

## Modifying the Script

If you need to modify how the requirements files are generated, edit the `generate_requirements.sh` script. The current implementation:

- Exports all dependencies to `requirements.txt`
- Exports only dev dependencies to `dev-requirements.txt`
- Does not include hashes in the exported files
