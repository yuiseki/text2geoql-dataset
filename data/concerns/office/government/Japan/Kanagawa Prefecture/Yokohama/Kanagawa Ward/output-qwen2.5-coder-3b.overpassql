[out:json][timeout:30];
area["name:en"="Kanagawa Prefecture"]->.outer;
area["name:ja"="神奈川県"]->.inner;
(
  nwr["office"~"government"](area.inner)(area.outer);
);
out geom;
