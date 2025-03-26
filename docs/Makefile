.PHONY: docs docs-serve docs-pdf clean-docs

DOCS_DIR = .
BUILD_DIR = $(DOCS_DIR)/_build
SOURCE_DIR = $(DOCS_DIR)/source

SPHINX_BUILD = poetry run sphinx-build
SPHINX_OPTS = -W -b

docs:
	@echo "Gerando documentação HTML..."
	@echo "Source Dir: $(SOURCE_DIR)"
	@echo "Build Dir: $(BUILD_DIR)/html"
	$(SPHINX_BUILD) $(SPHINX_OPTS) html $(SOURCE_DIR) $(BUILD_DIR)/html

docs-serve:
	@echo "Servindo documentação em http://localhost:8000"
	cd $(BUILD_DIR)/html && python -m http.server 8000

#docs-pdf:
#	@echo "Gerando documentação em PDF..."
#	$(SPHINX_BUILD) $(SPHINX_OPTS) latexpdf $(SOURCE_DIR) $(BUILD_DIR)/pdf

clean-docs:
	@echo "Limpando documentação gerada..."
	rm -rf $(BUILD_DIR)/*

terraform-docs:
	@echo "Gerando documentação do Terraform..."
	mkdir -p ./terraform
	terraform-docs markdown ../infra | pandoc -f markdown -t rst -o ./source/infra.rst
	sed -i '1i========================\nInfraestrutura Terraform\n========================\n' ./source/infra.rst
	terraform-docs markdown ../init | pandoc -f markdown -t rst -o ./source/init.rst
	sed -i '1i=======================\nInicialização Terraform\n=======================\n' ./source/init.rst

all-docs: clean-docs terraform-docs docs