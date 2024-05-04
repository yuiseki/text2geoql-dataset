[out:json][timeout:30000];
area["name:en"="Niigata"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
