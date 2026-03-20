[out:json][timeout:30];
area["name:en"="Municipality of Pristina"]->.outer;
area["name:en"="Pristina"]
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;
