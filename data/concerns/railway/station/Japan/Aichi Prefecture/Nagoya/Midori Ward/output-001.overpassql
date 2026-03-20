[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Midori Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
