[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Fukuoka Prefecture"]->.inner;
(
  nwr["cuisine"~"thai"](area.inner)(area.outer);
);
out geom;
