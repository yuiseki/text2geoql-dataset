[out:json][timeout:30];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Nakagawa Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
