/* Original synthetic ARM64-only JNI fixture. */
#include <jni.h>
#include <stdint.h>

#if !defined(__aarch64__)
#error This fixture must be built as AArch64, not x86.
#endif

JNIEXPORT jint JNICALL
Java_org_raft_qa_armfixture_ArmProbe_transform(JNIEnv *env, jclass clazz, jint value) {
    (void)env;
    (void)clazz;
    return (jint)(((uint32_t)value ^ UINT32_C(0x12345678)) + UINT32_C(17));
}

#ifdef RAFT_ANDROID_JNI_LOG
int raft_vulkan_probe_main(void);

JNIEXPORT jint JNICALL
Java_org_raft_qa_armfixture_ArmProbe_runVulkan(JNIEnv *env, jclass clazz) {
    (void)env;
    (void)clazz;
    return raft_vulkan_probe_main();
}
#endif
