class A { void f(HttpServletRequest req) throws Exception { ScriptEngine e = mgr.getEngineByName("js"); e.eval(req.getParameter("expr")); } }
