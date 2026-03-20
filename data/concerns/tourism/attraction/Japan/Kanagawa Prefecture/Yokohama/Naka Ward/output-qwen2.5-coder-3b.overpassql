[out:json][timeout:30];
area["name:en"="Naka Ward"][boundary=administrative]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["tourism"="attraction"](area.inner)(area.outer);
);
out geom;
