import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global
import scala.util.{Failure, Success}

object ScalaFuture extends App {

  val finiraPlusTard = Future {
    ... // tâche longue
  }

  finiraPlusTard.onComplete {
    case Success(valeur) => traiterValeurDeRetour(valeur)
    case Failure(exception) => gererException(exception)
  }

  Thread.sleep(2000)  // "garder en vie" le runtime
}
