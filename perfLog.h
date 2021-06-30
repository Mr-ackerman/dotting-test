#include <mutex>
#include <string>

class PerfLog {
public:
  static PerfLog& GetInstance() {
    static std::once_flag s_flag;
    std::call_once(s_flag, [&]() {
      instance_.reset(new PerfLog);
    });

    return *instance_;
  }
  PerfLog();
  ~PerfLog() = default;

  void SyslogPrintStart(std::string rangeDes, std::string func, int line);
  void SyslogPrintEnd(std::string rangeDes, std::string func, int line);

private:
  static std::unique_ptr<PerfLog> instance_;
  bool m_isDebug;

};

#define DEBUG

#ifdef DEBUG
#define PERF_PRINT_START(des) \
  { \
    PerfLog::GetInstance().SyslogPrintStart(des, __FUNCTION__, __LINE__); \
  }

#define PERF_PRINT_END(des) \
  { \
    PerfLog::GetInstance().SyslogPrintEnd(des, __FUNCTION__, __LINE__); \
  }
#else
  #define PERF_PRINT_START(des)
  #define PERF_PRINT_END(des)
#endif


