testclean: clean
	@rm -rf __pycache__
	@rm -rf results.xml
	@rm -rf combined_results.xml
	@rm -rf log.txt
	@rm -rf sim_build
	@rm -rf modelsim.ini
	@rm -rf transcript
	@rm -rf results
	@rm -rf simulation.vcd

checkclean: check testclean

