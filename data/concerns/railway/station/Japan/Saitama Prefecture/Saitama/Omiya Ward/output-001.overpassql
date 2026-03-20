[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Omiya Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
