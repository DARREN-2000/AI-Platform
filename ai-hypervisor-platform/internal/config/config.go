package config

type Config struct {
	Logging     interface{}
	Environment interface{}
}

func Load() (*Config, error) {
	return &Config{}, nil
}
