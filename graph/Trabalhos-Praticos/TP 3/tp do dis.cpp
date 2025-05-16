
    private boolean getCaminhosDisjuntoRecursive(Point startPoint, Point endPoint, List<Point> path, List<Edge> edgesVisited,List<Point> pointsVisited) {

        boolean pathComplete = false;

        if (startPoint.equals(endPoint)) {
            path.add(endPoint);
            return true ;
        }
        for (String pointName : startPoint.getGoing().keySet()) {
            Point point = startPoint.getGoing().get(pointName);
            String edgeName = startPoint.getName() + ":" + pointName;
            Edge goingEdge = this.edges.get(edgeName);
            System.err.println("olhando a edge: "+edgeName);

            if (goingEdge != null && !edgesVisited.contains(goingEdge) && !pointsVisited.contains(startPoint)) {
                path.add(startPoint);
//                pointsVisited.add(startPoint);

                edgesVisited.add(goingEdge);
                System.err.println("adicionando a edge: "+edgeName);
                for (String name : point.getGoing().keySet()) {
                    path.add(point);
                    pointsVisited.add(point);

                    pathComplete = getCaminhosDisjuntoRecursive(point.getGoing().get(name), endPoint, path, edgesVisited,pointsVisited);
                    if(pathComplete) {
                        break;
                    }
                }
            }
            if(pathComplete||path.contains(endPoint)){
                break;
            }
        }
        return false;
    }