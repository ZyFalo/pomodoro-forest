@echo off
echo Ejecutando script de migración para árboles...
python -m backend.migration_tree_templates
echo Migración completada!
pause
