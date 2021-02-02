# s3cmd rm \
#     --force \
#     --recursive \
#     s3://fieldmapsdata/global-admin/

s3cmd put \
    --acl-public \
    3_exports/10_export_compress/wld_points.gpkg.zip \
    s3://fieldmapsdata/global-admin/wld_points.gpkg.zip

s3cmd put \
    --acl-public \
    3_exports/10_export_compress/wld_lines.gpkg.zip \
    s3://fieldmapsdata/global-admin/wld_lines.gpkg.zip

s3cmd put \
    --acl-public \
    3_exports/10_export_compress/wld_polygons.gpkg.zip \
    s3://fieldmapsdata/global-admin/wld_polygons.gpkg.zip

s3cmd put \
    --acl-public \
    3_exports/10_export_compress/wld_points.gdb.zip \
    s3://fieldmapsdata/global-admin/wld_points.gdb.zip

s3cmd put \
    --acl-public \
    3_exports/10_export_compress/wld_lines.gdb.zip \
    s3://fieldmapsdata/global-admin/wld_lines.gdb.zip

s3cmd put \
    --acl-public \
    3_exports/10_export_compress/wld_polygons.gdb.zip \
    s3://fieldmapsdata/global-admin/wld_polygons.gdb.zip

s3cmd put \
    --acl-public \
    --recursive \
    --exclude '.DS_Store' \
    3_exports/10_export_compress/voronoi/* \
    s3://fieldmapsdata/global-admin/voronoi/

# s3cmd sync \
#     --acl-public \
#     --delete-removed \
#     --exclude '.DS_Store' \
#     3_exports/10_export_compress/ \
#     s3://fieldmapsdata/global-admin/
