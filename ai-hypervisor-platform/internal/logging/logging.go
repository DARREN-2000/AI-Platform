package logging

import "github.com/sirupsen/logrus"

func NewLogger(env string, cfg interface{}) *logrus.Logger {
	return logrus.New()
}
