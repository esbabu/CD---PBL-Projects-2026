; ModuleID = 'tests/secure_safe_functions.c'
source_filename = "tests/secure_safe_functions.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.FirmwarePackage = type { i32, [16 x i8], [128 x i8], [32 x i8] }

@current_version = dso_local global i32 10, align 4
@.str = private unnamed_addr constant [20 x i8] c"https://github.com/\00", align 1
@__const.main.pkg = private unnamed_addr constant %struct.FirmwarePackage { i32 11, [16 x i8] c"prod\00\00\00\00\00\00\00\00\00\00\00\00", [128 x i8] c"https://github.com/trusted/firmware.bin\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00\00", [32 x i8] zeroinitializer }, align 4
@.str.1 = private unnamed_addr constant [5 x i8] c"v=%d\00", align 1

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
  %4 = getelementptr inbounds %struct.FirmwarePackage, ptr %3, i32 0, i32 2
  %5 = getelementptr inbounds [128 x i8], ptr %4, i64 0, i64 0
  %6 = call i32 @strncmp(ptr noundef %5, ptr noundef @.str, i64 noundef 19) #4
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
define dso_local i32 @updateFirmware(ptr noundef %0) #0 {
  %2 = alloca i32, align 4
  %3 = alloca ptr, align 8
  store ptr %0, ptr %3, align 8
  %4 = load ptr, ptr %3, align 8
  call void @sanitizePackage(ptr noundef %4)
  %5 = load ptr, ptr %3, align 8
  %6 = call i32 @verifySignature(ptr noundef %5)
  %7 = icmp ne i32 %6, 0
  br i1 %7, label %9, label %8

8:                                                ; preds = %1
  store i32 -1, ptr %2, align 4
  br label %28

9:                                                ; preds = %1
  %10 = load ptr, ptr %3, align 8
  %11 = call i32 @sourceTrusted(ptr noundef %10)
  %12 = icmp ne i32 %11, 0
  br i1 %12, label %14, label %13

13:                                               ; preds = %9
  store i32 -2, ptr %2, align 4
  br label %28

14:                                               ; preds = %9
  %15 = load ptr, ptr %3, align 8
  %16 = getelementptr inbounds %struct.FirmwarePackage, ptr %15, i32 0, i32 0
  %17 = load i32, ptr %16, align 4
  %18 = load i32, ptr @current_version, align 4
  %19 = icmp sle i32 %17, %18
  br i1 %19, label %20, label %21

20:                                               ; preds = %14
  store i32 -3, ptr %2, align 4
  br label %28

21:                                               ; preds = %14
  %22 = load ptr, ptr %3, align 8
  %23 = call i32 @verifyImageHash(ptr noundef %22)
  %24 = icmp ne i32 %23, 0
  br i1 %24, label %26, label %25

25:                                               ; preds = %21
  store i32 -4, ptr %2, align 4
  br label %28

26:                                               ; preds = %21
  %27 = load ptr, ptr %3, align 8
  call void @install(ptr noundef %27)
  store i32 0, ptr %2, align 4
  br label %28

28:                                               ; preds = %26, %25, %20, %13, %8
  %29 = load i32, ptr %2, align 4
  ret i32 %29
}

; Function Attrs: noinline nounwind uwtable
define internal void @sanitizePackage(ptr noundef %0) #0 {
  %2 = alloca ptr, align 8
  %3 = alloca [16 x i8], align 16
  %4 = alloca [64 x i8], align 16
  %5 = alloca [32 x i8], align 16
  store ptr %0, ptr %2, align 8
  %6 = getelementptr inbounds [16 x i8], ptr %3, i64 0, i64 0
  %7 = load ptr, ptr %2, align 8
  %8 = getelementptr inbounds %struct.FirmwarePackage, ptr %7, i32 0, i32 1
  %9 = getelementptr inbounds [16 x i8], ptr %8, i64 0, i64 0
  %10 = call i32 @strncpy_s(ptr noundef %6, i64 noundef 16, ptr noundef %9, i64 noundef 15)
  %11 = getelementptr inbounds [64 x i8], ptr %4, i64 0, i64 0
  %12 = load ptr, ptr %2, align 8
  %13 = getelementptr inbounds %struct.FirmwarePackage, ptr %12, i32 0, i32 0
  %14 = load i32, ptr %13, align 4
  %15 = call i32 (ptr, i64, ptr, ...) @snprintf(ptr noundef %11, i64 noundef 64, ptr noundef @.str.1, i32 noundef %14) #5
  %16 = getelementptr inbounds [32 x i8], ptr %5, i64 0, i64 0
  %17 = load ptr, ptr %2, align 8
  %18 = getelementptr inbounds %struct.FirmwarePackage, ptr %17, i32 0, i32 3
  %19 = getelementptr inbounds [32 x i8], ptr %18, i64 0, i64 0
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %16, ptr align 4 %19, i64 32, i1 false)
  ret void
}

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca %struct.FirmwarePackage, align 4
  store i32 0, ptr %1, align 4
  call void @llvm.memcpy.p0.p0.i64(ptr align 4 %2, ptr align 4 @__const.main.pkg, i64 180, i1 false)
  %3 = call i32 @updateFirmware(ptr noundef %2)
  ret i32 %3
}

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #2

; Function Attrs: noinline nounwind uwtable
define internal i32 @strncpy_s(ptr noundef %0, i64 noundef %1, ptr noundef %2, i64 noundef %3) #0 {
  %5 = alloca i32, align 4
  %6 = alloca ptr, align 8
  %7 = alloca i64, align 8
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  store ptr %0, ptr %6, align 8
  store i64 %1, ptr %7, align 8
  store ptr %2, ptr %8, align 8
  store i64 %3, ptr %9, align 8
  %11 = load ptr, ptr %6, align 8
  %12 = icmp ne ptr %11, null
  br i1 %12, label %13, label %19

13:                                               ; preds = %4
  %14 = load ptr, ptr %8, align 8
  %15 = icmp ne ptr %14, null
  br i1 %15, label %16, label %19

16:                                               ; preds = %13
  %17 = load i64, ptr %7, align 8
  %18 = icmp eq i64 %17, 0
  br i1 %18, label %19, label %20

19:                                               ; preds = %16, %13, %4
  store i32 -1, ptr %5, align 4
  br label %53

20:                                               ; preds = %16
  store i64 0, ptr %10, align 8
  br label %21

21:                                               ; preds = %39, %20
  %22 = load i64, ptr %10, align 8
  %23 = load i64, ptr %9, align 8
  %24 = icmp ult i64 %22, %23
  br i1 %24, label %25, label %37

25:                                               ; preds = %21
  %26 = load i64, ptr %10, align 8
  %27 = add i64 %26, 1
  %28 = load i64, ptr %7, align 8
  %29 = icmp ult i64 %27, %28
  br i1 %29, label %30, label %37

30:                                               ; preds = %25
  %31 = load ptr, ptr %8, align 8
  %32 = load i64, ptr %10, align 8
  %33 = getelementptr inbounds i8, ptr %31, i64 %32
  %34 = load i8, ptr %33, align 1
  %35 = sext i8 %34 to i32
  %36 = icmp ne i32 %35, 0
  br label %37

37:                                               ; preds = %30, %25, %21
  %38 = phi i1 [ false, %25 ], [ false, %21 ], [ %36, %30 ]
  br i1 %38, label %39, label %49

39:                                               ; preds = %37
  %40 = load ptr, ptr %8, align 8
  %41 = load i64, ptr %10, align 8
  %42 = getelementptr inbounds i8, ptr %40, i64 %41
  %43 = load i8, ptr %42, align 1
  %44 = load ptr, ptr %6, align 8
  %45 = load i64, ptr %10, align 8
  %46 = getelementptr inbounds i8, ptr %44, i64 %45
  store i8 %43, ptr %46, align 1
  %47 = load i64, ptr %10, align 8
  %48 = add i64 %47, 1
  store i64 %48, ptr %10, align 8
  br label %21, !llvm.loop !6

49:                                               ; preds = %37
  %50 = load ptr, ptr %6, align 8
  %51 = load i64, ptr %10, align 8
  %52 = getelementptr inbounds i8, ptr %50, i64 %51
  store i8 0, ptr %52, align 1
  store i32 0, ptr %5, align 4
  br label %53

53:                                               ; preds = %49, %19
  %54 = load i32, ptr %5, align 4
  ret i32 %54
}

; Function Attrs: nounwind
declare i32 @snprintf(ptr noundef, i64 noundef, ptr noundef, ...) #3

attributes #0 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nounwind willreturn memory(read) "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #3 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind willreturn memory(read) }
attributes #5 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 2}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 18.1.3 (1ubuntu1)"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
