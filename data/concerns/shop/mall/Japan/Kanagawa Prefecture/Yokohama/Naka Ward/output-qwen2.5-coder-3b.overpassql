[out:json][timeout:30];
area["name:en"="Naka Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
