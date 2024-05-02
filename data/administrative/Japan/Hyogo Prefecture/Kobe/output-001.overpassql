[out:json][timeout:30000];
area["name:en"="Hyogo Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Kobe"](area.searchArea);
);
out geom;
