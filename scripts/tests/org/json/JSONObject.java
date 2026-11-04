package org.json;
import java.util.LinkedHashMap;
import java.util.Map;
/** JVM regression-only test adapter, not part of app sources or APK. */
public final class JSONObject {
    private final Map<String,Object> map=new LinkedHashMap<>();
    public JSONObject put(String key,Object value){map.put(key,value);return this;}
    public boolean has(String key){return map.containsKey(key);}
    public JSONObject getJSONObject(String key){return (JSONObject)map.get(key);}
    public long getLong(String key){return ((Number)map.get(key)).longValue();}
}
