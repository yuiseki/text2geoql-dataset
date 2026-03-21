[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["office"~"government"](area.inner)(area.outer);
);
out geom;
