#include <sys/time.h>
#include <unistd.h>
#include <syslog.h>
#include <stdio.h>
#include <fstream>
#include <sstream>
#include <sys/syscall.h>
#include "perfLog.h"


#define gettid() syscall(__NR_gettid)

#define MODULE "proc_accel"
#define PATH_DEBUG "/var/debug"

static long long getCurrentTime() {

  struct timeval time_curr;

  gettimeofday(&time_curr, NULL);

  return (long long)time_curr.tv_sec * 1000 + time_curr.tv_usec / 1000;
}

std::unique_ptr<PerfLog> PerfLog::instance_ = nullptr;

PerfLog::PerfLog() {
  std::ifstream fin(PATH_DEBUG);
    if (fin.good()) {
      m_isDebug = true;
    } else {
      m_isDebug = false;
    }

};

// perfBreak:{"func" : "abc", "ppid" : 1230, "pid" : 12340, "tid" : 12341, "flag" : 1, "time" : 1131, "range" : "abc"}
void PerfLog::SyslogPrintStart(std::string rangeDes, std::string func, int line) {
  if (!m_isDebug) {
    return;
  }

  std::stringstream ostr;

  ostr  << "perfBreak:{"
  << "\"func\":\"" << func << "\","
  << "\"line\":" << line << ","
  << "\"ppid\":" << getppid() << ","
  << "\"pid\":"  << getpid() << ","
  << "\"tid\":"  << gettid() << ","
  << "\"flag\":" << 0 << ","
  << "\"time\":" << getCurrentTime() << ","
  << "\"range\":\""  << rangeDes << "\""
  << "}";

  openlog(MODULE, LOG_PID, LOG_USER);
  syslog(LOG_CRIT, "%s", ostr.str().c_str());
  closelog();

}

void PerfLog::SyslogPrintEnd(std::string rangeDes, std::string func, int line) {
  if (!m_isDebug) {
    return;
  }

  std::stringstream ostr;

  ostr  << "perfBreak:{"
  << "\"func\":\"" << func << "\","
  << "\"line\":" << line << ","
  << "\"ppid\":" << getppid() << ","
  << "\"pid\":"  << getpid() << ","
  << "\"tid\":"  << gettid() << ","
  << "\"flag\":" << 1 << ","
  << "\"time\":" << getCurrentTime() << ","
  << "\"range\":\""  << rangeDes << "\""
  << "}";

  openlog(MODULE, LOG_PID, LOG_USER);
  syslog(LOG_CRIT, "%s", ostr.str().c_str());
  closelog();

}



