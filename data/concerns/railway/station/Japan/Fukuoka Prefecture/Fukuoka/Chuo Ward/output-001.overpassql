[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
