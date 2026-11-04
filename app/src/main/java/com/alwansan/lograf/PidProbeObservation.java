package com.alwansan.lograf;

/**
 * Separate an explicitly empty pidof result from a failed or unverified
 * process probe. -2 means UNKNOWN, not an app death.
 */
final class PidProbeObservation {
    static final int UNKNOWN=-2;
    static final int NOT_RUNNING=-1;
    private PidProbeObservation(){}
    static int gamePid(int verifiedMainPid,String probeStatus){
        if(verifiedMainPid>0)return verifiedMainPid;
        return "pidof_empty".equals(probeStatus)?NOT_RUNNING:UNKNOWN;
    }
}
