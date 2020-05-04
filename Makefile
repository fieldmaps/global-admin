# Commands intended for project owner
compress_input_attributes:
	mkdir -p 0_data_outputs
	rm -f 0_data_outputs/input_attributes.zip
	cd 0_data_inputs/attributes && \
	zip -x '*.DS_Store' -r ../../0_data_outputs/input_attributes.zip .
compress_input_boundaries:
	mkdir -p 0_data_outputs
	rm -f 0_data_outputs/input_boundaries.zip
	cd 0_data_inputs/boundaries && \
	zip -x '*.DS_Store' -r ../../0_data_outputs/input_boundaries.zip .
compress_hdx_attributes:
	mkdir -p 0_data_outputs
	rm -f 0_data_outputs/hdx_attributes.zip
	cd 1_admin_attributes/3_export_hdx && \
	zip -x '*.DS_Store' -r ../../0_data_outputs/hdx_attributes.zip .
compress_wld_xlsx:
	mkdir -p 0_data_outputs
	rm -f 0_data_outputs/wld.xlsx.zip
	cd 1_admin_attributes/2_merge_sources && \
	zip -x '*.DS_Store' -r ../../0_data_outputs/wld.xlsx.zip .
sync:
	aws s3 sync 0_data_outputs s3://fieldmaps-data/global-admin --exclude '*.DS_Store'

# Retrieve remote data
get_attributes:
	make download_attributes
	make extract_attributes
get_boundaries:
	make download_boundaries
	make extract_boundaries
download_attributes:
	mkdir -p 0_data_inputs
	curl https://data.fieldmaps.io/global-admin/input_attributes.zip \
		--output 0_data_inputs/input_attributes.zip
download_boundaries:
	mkdir -p 0_data_inputs
	curl https://data.fieldmaps.io/global-admin/input_boundaries.zip \
		--output 0_data_inputs/input_boundaries.zip
extract_attributes:
	rm -rf 0_data_inputs/attributes
	unzip 0_data_inputs/input_attributes.zip -d 0_data_inputs/attributes
	rm -f 0_data_inputs/input_attributes.zip
extract_boundaries:
	rm -rf 0_data_inputs/boundaries
	unzip 0_data_inputs/input_boundaries.zip -d 0_data_inputs/boundaries
	rm -f 0_data_inputs/input_boundaries.zip

# Run Python scripts sequentially
build_attributes:
	python3 1_admin_attributes/1_import_gadm.py
	python3 1_admin_attributes/1_import_hdx.py
	python3 1_admin_attributes/2_merge_sources.py
	python3 1_admin_attributes/3_export_hdx.py