from tools.backdoor_validation.one_backdoor.main import initialize_backdoor, parse_arguments, initialize_model

backdoor = initialize_backdoor()
instance_format, file = parse_arguments()
model = initialize_model(instance_format, file)

model.optimize()
