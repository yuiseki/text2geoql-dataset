[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kohoku Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
