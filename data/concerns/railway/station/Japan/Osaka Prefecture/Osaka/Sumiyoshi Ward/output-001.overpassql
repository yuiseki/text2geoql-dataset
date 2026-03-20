[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Sumiyoshi Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
