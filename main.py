import json
import os
import sys
import traceback

class Quiz:
    def __init__(self, question: str, choices: list, answer: int):
        self.question = question
        self.choices = choices
        self.answer = int(answer)

    def display(self, index):
        print(f"\n문제 {index}. {self.question}")
        for i, choice in enumerate(self.choices, 1):
            print(f"  {i}) {choice}")

    def is_correct(self, user_answer):
        return self.answer == user_answer

    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }

class QuizGame:
    def __init__(self):
        self.file_path = "state.json"
        self.quizzes = []
        self.best_score = None
        self.load_data()

    def load_data(self):
        default_quizzes = [
            {"question": "현재 작업 중인 디렉토리의 전체 경로를 확인할 때 사용하는 리눅스 명령어는 무엇인가?", "choices": ["ls", "pwd", "cd", "whoami"], "answer": 2},
            {"question": "파일이나 디렉토리의 접근 권한을 변경할 때 사용하는 리눅스 명령어는 무엇인가?", "choices": ["chmod", "chown", "touch", "find"], "answer": 1},
            {"question": "Docker에서 현재 실행 중인 컨테이너 목록을 확인할 때 사용하는 명령어는 무엇인가?", "choices": ["docker images", "docker run", "docker ps", "docker build"], "answer": 3},
            {"question": "Git에서 새로운 브랜치를 생성할 때 사용하는 명령어는 무엇인가?", "choices": ["git merge", "git branch", "git clone", "git reset"], "answer": 2},
            {"question": "Git에서 작업 디렉토리와 스테이징 영역의 상태를 확인할 때 사용하는 명령어는 무엇인가?", "choices": ["git push", "git status", "git log", "git diff"], "answer": 2}
        ]

        if not os.path.exists(self.file_path):
            self.quizzes = [Quiz(**q) for q in default_quizzes]
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.quizzes = [Quiz(**q) for q in data.get("quizzes", [])]
                self.best_score = data.get("best_score", 0)
        except (json.JSONDecodeError, IOError):
            print("\n[알림] 데이터 파일이 손상되었거나 읽을 수 없습니다.")
            while True:
                user_input = input("기본 데이터로 초기화할까요? (y/n): ").lower().strip()
    
                if user_input == 'y':
                    self.quizzes = [Quiz(**q) for q in default_quizzes]
                    if self.save_data():
                        print("기본 데이터로 초기화되었습니다.")
                        break
                    else:
                        print("기본 데이터로 초기화에 실패했습니다.")
                    
                elif user_input == 'n':
                    print("초기화를 취소합니다. 기존 파일을 수동으로 점검해주세요.")
                    break  # 루프 탈출
                else:
                    print("잘못된 입력입니다. 'y' 또는 'n'만 입력해주세요.")
                

    def save_data(self):
        try:
            json_data = json.dumps({
            "quizzes": [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score
            }, ensure_ascii=False, indent=4)
        except (TypeError, ValueError) as e:
            print(f"[데이터 오류] JSON 변환에 실패했습니다: {e}")
            return False

        temp_file = self.file_path + ".tmp"

        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(json_data)
                f.flush() 
                os.fsync(f.fileno())
            
            os.replace(temp_file, self.file_path)
            print("[저장 완료] 데이터가 안전하게 업데이트되었습니다.")
            return True
        
        except Exception as e:
            print(f"\n[저장 실패] 데이터 보존을 위해 기존 파일을 유지합니다. 에러: {e}")
            traceback.print_exc()
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False

    def safe_input(self, prompt, range_min=0, range_max=0):
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input:
                    print("비어 있는 입력입니다. 다시 입력해주세요.")
                    continue
                
                val = int(user_input)
                if range_min is not None and (val < range_min or val > range_max):
                    print(f"범위 오류 ({range_min}~{range_max} 사이 숫자를 입력하세요).")
                    continue
                return val
            except ValueError:
                print("숫자만 입력 가능합니다. 다시 시도하세요.")
            except (EOFError, KeyboardInterrupt):
                if self.save_data():
                    print("데이터가 안전하게 저장되었습니다. 프로그램을 종료합니다.")
                    sys.exit(0)
                else:
                    print("데이터 저장에 실패했습니다!")
                    sys.exit(1)
                    


                

    def play_game(self):
        if not self.quizzes:
            print("\n출제할 문제가 없습니다. 문제를 추가해주세요.")
            return

        score = 0
        print("\n--- 퀴즈를 시작합니다! ---")
        for i, q in enumerate(self.quizzes, 1):
            q.display(i)
            ans = self.safe_input("정답 번호 입력: ", 1, 4)
            if q.is_correct(ans):
                print("정답입니다!")
                score += 1
            else:
                print(f"틀렸습니다. 정답은 {q.answer}번입니다.")

        print(f"\n최종 점수: {score} / {len(self.quizzes)}")
        if self.best_score is None or score > self.best_score:
            prev_record = "없음" if self.best_score is None else self.best_score
            print(f"🎊 축하합니다! 새로운 최고 기록 달성! (이전 기록: {prev_record})")
            self.best_score = score
            if self.save_data():
                print("기록이 안전하게 저장되었습니다.")
            else:
                print("기록 저장에 실패했습니다.")
        else:
            print(f"현재 최고 기록은 {self.best_score}점입니다. 다음 기회에 도전하세요!")

    def add_quiz(self):
        print("\n--- 새 퀴즈 추가 ---")
        question = input("문제 내용을 입력하세요: ").strip()
        choices = []
        for i in range(1, 5):
            choices.append(input(f"선택지 {i} 입력: ").strip())
        answer = self.safe_input("정답 번호(1~4) 입력: ", 1, 4)
        
        self.quizzes.append(Quiz(question, choices, answer))
        if self.save_data():
            print("퀴즈가 성공적으로 등록되었습니다.")
        else:
            print("퀴즈 등록에 실패했습니다.")
   
    def show_list(self):
        print("\n--- 등록된 퀴즈 목록 ---")
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        for i, q in enumerate(self.quizzes, 1):
            print(f"{i}. {q.question}")

    def show_best_score(self):
        print(f"\n현재 최고 점수: {self.best_score}점")

    def run(self):
        while True:
            print("\n===== 퀴즈 게임 메뉴 =====")
            print("1. 퀴즈 풀기")
            print("2. 퀴즈 등록")
            print("3. 퀴즈 목록")
            print("4. 최고 점수 확인")
            print("5. 종료")
            print("==========================")
            
            choice = self.safe_input("메뉴 선택: ", 1, 5)
            
            if choice == 1: self.play_game()
            elif choice == 2: self.add_quiz()
            elif choice == 3: self.show_list()
            elif choice == 4: self.show_best_score()
            elif choice == 5:
                print("게임을 종료합니다.")
                self.save_data()
                break       

if __name__ == "__main__":
    game = QuizGame()
    game.load_data()
    game.run()
