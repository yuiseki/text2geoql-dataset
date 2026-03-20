[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Nakagyo Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
