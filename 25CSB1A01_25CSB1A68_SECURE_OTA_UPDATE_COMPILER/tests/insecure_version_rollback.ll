; ModuleID = 'tests/insecure_version_rollback.c'
source_filename = "tests/insecure_version_rollback.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.DeviceState = type { i32 }
%struct.FirmwarePackage = type { i32, [16 x i8], [16 x i8], [128 x i8], [32 x i8], [64 x i8], i32 }

@current_version = dso_local global i32 65792, align 4
@s_nvram_version = internal global i32 65792, align 4
@.str = private unnamed_addr constant [20 x i8] c"https://github.com/\00", align 1
@__const.main.dev = private unnamed_addr constant %struct.DeviceState { i32 65792 }, align 4
@__const.main.pkg = private unnamed_addr constant %struct.FirmwarePackage { i32 65536, [16 x i8] c"1.0.0\00\00\00\00\00\00\00\00\00\00\00", [16 x i8] c"stable\00\00\00\00\00\00\00\00\00\00", [128 x i8] c"https://github.com/firmware/v1.0.0.bin\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00", [32 x i8] zeroinitializer, [64 x i8] zeroinitializer, i32 512 }, align 4

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @get_current_firmware_version() #0 {
  %1 = load i32, ptr @s_nvram_version, align 4
  ret i32 %1
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @set_current_firmware_version(i32 noundef %0) #0 {
  %2 = alloca i32, align 4
  store i32 %0, ptr %2, align 4
  %3 = load i32, ptr %2, align 4
  store i32 %3, ptr @s_nvram_version, align 4
  %4 = load i32, ptr %2, align 4
  store i32 %4, ptr @current_version, align 4
  ret i32 0
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @verifySignature(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  ret i32 1
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @sourceTrusted(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds %struct.FirmwarePackage, ptr %3, i32 0, i32 3
  %5 = getelementptr inbounds [128 x i8], ptr %4, i64 0, i64 0
  %6 = call i32 @strncmp(ptr noundef %5, ptr noundef @.str, i64 noundef 19) #3
  %7 = icmp eq i32 %6, 0
  %8 = zext i1 %7 to i32
  ret i32 %8
}

; Function Attrs: nounwind willreturn memory(read)
declare i32 @strncmp(ptr noundef, ptr noundef, i64 noundef) #1

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @verifyImageHash(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  ret i32 1
}

; Function Attrs: noinline nounwind uwtable
define dso_local void @install(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  %3 = load ptr, ptr %2, align 8
  ret void
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @updateFirmware(ptr noundef %0, ptr noundef %1) #0 {
  %3 = alloca i32, align 4
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  %7 = load ptr, ptr %5, align 8
  %8 = call i32 @verifySignature(ptr noundef %7)
  %9 = icmp ne i32 %8, 0
  br i1 %9, label %11, label %10

10:                                               ; preds = %2
  store i32 -1, ptr %3, align 4
  br label %35

11:                                               ; preds = %2
  %12 = load ptr, ptr %5, align 8
  %13 = call i32 @sourceTrusted(ptr noundef %12)
  %14 = icmp ne i32 %13, 0
  br i1 %14, label %16, label %15

15:                                               ; preds = %11
  store i32 -2, ptr %3, align 4
  br label %35

16:                                               ; preds = %11
  %17 = load ptr, ptr %5, align 8
  %18 = call i32 @verifyImageHash(ptr noundef %17)
  %19 = icmp ne i32 %18, 0
  br i1 %19, label %21, label %20

20:                                               ; preds = %16
  store i32 -3, ptr %3, align 4
  br label %35

21:                                               ; preds = %16
  %22 = load ptr, ptr %5, align 8
  call void @install(ptr noundef %22)
  %23 = load ptr, ptr %5, align 8
  %24 = getelementptr inbounds %struct.FirmwarePackage, ptr %23, i32 0, i32 0
  %25 = load i32, ptr %24, align 4
  store i32 %25, ptr %6, align 4
  %26 = load i32, ptr %6, align 4
  %27 = call i32 @set_current_firmware_version(i32 noundef %26)
  %28 = load ptr, ptr %4, align 8
  %29 = icmp ne ptr %28, null
  br i1 %29, label %30, label %34

30:                                               ; preds = %21
  %31 = load i32, ptr %6, align 4
  %32 = load ptr, ptr %4, align 8
  %33 = getelementptr inbounds %struct.DeviceState, ptr %32, i32 0, i32 0
  store i32 %31, ptr %33, align 4
  br label %34

34:                                               ; preds = %30, %21
  store i32 0, ptr %3, align 4
  br label %35

35:                                               ; preds = %34, %20, %15, %10
  %36 = load i32, ptr %3, align 4
  ret i32 %36
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca %struct.DeviceState, align 4
  %3 = alloca %struct.FirmwarePackage, align 4
  store i32 0, ptr %1, align 4
  call void @llvm.memcpy.p0.p0.i64(ptr align 4 %2, ptr align 4 @__const.main.dev, i64 4, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 4 %3, ptr align 4 @__const.main.pkg, i64 264, i1 false)
  %4 = call i32 @updateFirmware(ptr noundef %2, ptr noundef %3)
  ret i32 %4
}

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #2

attributes #0 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nounwind willreturn memory(read) "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #3 = { nounwind willreturn memory(read) }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 18.1.3 (1ubuntu1)"}
