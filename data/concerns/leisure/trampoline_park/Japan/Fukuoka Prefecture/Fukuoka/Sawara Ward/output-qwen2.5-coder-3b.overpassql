[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Fukuoka Prefecture"]->.inner;
(
  nwr["leisure"="trampoline_park"](area.inner)(area.outer);
);
out geom;
