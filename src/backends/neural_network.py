import pickle
import neat

def unpack_agent(serialized_agent):
    # Deserialize the network
    print("deserializing...")
    genome_key, network = pickle.loads(serialized_agent)

    return genome_key, network

def run_activations(network, inputs):
    # Run the network on the inputs
    print("4: class of network is:", type(network))
    output = network.activate(inputs)

    return output

def main():
    # This is where you would receive the serialized genome and config from the client.
    # For this example, we'll just use placeholders.
    pass

if __name__ == "__main__":
    main()