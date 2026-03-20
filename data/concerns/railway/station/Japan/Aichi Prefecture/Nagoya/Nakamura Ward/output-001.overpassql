[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Nakamura Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
