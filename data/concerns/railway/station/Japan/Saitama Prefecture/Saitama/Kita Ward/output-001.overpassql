[out:json][timeout:30000];
area["name:en"="Saitama"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
