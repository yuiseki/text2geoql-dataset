[out:json][timeout:30];
area["name:zh"="龙华区"]->.outer;
area["name:en"="Longhua District"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
