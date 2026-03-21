[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Shimogyo Ward"]->.inner;
(
  nwr["building"~"gate"](area.inner)(area.outer);
);
out geom;
