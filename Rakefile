tests = FileList[ 'test/**/test*.py' ]
puts "found #{tests.count} test files"
tests.each do |test|
    desc "run tests in #{test}"
    task test do
        sh "pytest #{test}"
    end
end

desc "run all tests"
task :test => tests
